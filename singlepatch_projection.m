addpath('/expanse/projects/nemar/yahya/MI_test/')
addpath('/home/jonton/Scripts/')
addpath('/expanse/projects/nemar/julie/eeglab2024.0/')
addpath('/expanse/projects/nemar/amica/')
addpath('/expanse/projects/nemar/julie/ForwardModelStuff/');
eeglab
 
forwardir = '/expanse/projects/nemar/julie/ForwardModelStuff/';
basedir = '/expanse/projects/nemar/julie/Results/';
 
% choose subject:
subjdir = 'OHSU_2020_11_13/';% subj 15, elecCoords_CS_32x32
%% Good components to forward project:
complist =  [1:6,8:11,13,15:17,19,20,23,24,25,27:32,36:38,40,47,48,50,51,53,60,62,67,70,71,73,75,77,79,80,81,83:85,88:90,94,95,98,99,100,103,108,110,113,115:120,121:124,126:137,140,141,143,144,146,149,150,154:158,160:168,171:176,179:202,205:213,215:218,220,222,223,224,226:235,237:242,244:248,250,252:254,256,257,259,261,266:271,273:284,286:288,290:302,304,306,309:313,315,316,318,319,322:325,328,329,331:336,340:342,344:349,351,352,356:360,362:365,368,372:376,377:383,385,387,388,390,392:395,397:413,415:429,431,432,433,436:440,441:444,446:448,450:455,457:460,462:464,467:483,485,487,488,490,491:495,497:506,509:514,516:518,520:528,530:537,539:547,551:553,555,558,559:569,571:576,579:586,588,589,592:598,601,603:605,607,608,610:615,617,618,622,623,625,626,628,631,632,634,635,638,639,641,642,646,648,649,650,651 653:658,660:674,678:686,688,689,691,692,696:698,702,703,704:712,715,717:719,721:724,726,727,729:734,737,739,740,743:747,749,750,752:760,765:766,767,768,773,774,776,778,779,783,786,790,795,796,797,799,802,803,804,805];% 807 grid data
gset = ['FullMotor_Only_RmChans.set']; % scalp projected EEG
EEG = pop_loadset('filename',gset,'filepath',[basedir,subjdir]);%% HP, then rm channels, then avg ref
EEG = pop_subcomp(EEG,complist,0,1);
EEG = pop_saveset( EEG,['FullMotor807chan582ICbp.set'], [basedir,subjdir]);
 
 
%% convert patch point activations to scalp sensor EEG:
EEG=[];ALLEEG=[];
pa = load([forwardir,'point_activationFull.mat']); % 485 x 787074
lfm = load([forwardir,'jcFS_s1_LFM.mat']);% 208 x 80150
 
%pamat = zeros(size(lfm.LFM,2),size(pa.point_activation,2)); % 80150 x 787074
pamat = sparse(size(lfm.LFM,2),size(pa.point_activation,2)); % 80150 x 787074
pamat(pa.LFM_indices,:) = pa.point_activation; % input sparse values
 
eegact = lfm.LFM*pamat; % 208 scalp sensors x 787074
clear pamat pa
 
sname = 'GridForward582-11-13';%sname = 'GridForward-11-13';
EEG = eeg_emptyset();
EEG.data = eegact;
EEG.pnts = size(EEG.data,2);
EEG.nbchan = size(EEG.data ,1);
EEG.srate = 1000;
EEG.condition = 'ecog';
EEG.filename = 'OHSU_2020_11_13_ForwardProjection';
EEG.filepath = [forwardir,sname,'.set'];
%EEG.setname = 'GridForward-11-13-DelNoiseICs'; % 248 chan grid
EEG.setname = sname; %
EEG=eeg_checkset(EEG);
EEG=pop_chanedit(EEG, 'load',{[forwardir,'sensors.dat'],'filetype','sfp'},'eval','chans = pop_chancenter( chans, [],[]);');
EEG = pop_select(EEG,'nochannel',1); % flatline
EEG = pop_saveset( EEG,[sname,'.set'], [forwardir]);
 
%% After forward projection on SCCN server python, save 208-chan dataset as:
% use EcogLRMtoScalp.m
dset = ['GridForward582-11-13.set'];%dset = ['GridForward-11-13.set'];
EEG = pop_loadset('filename',dset,'filepath',[forwardir]);%% HP, then rm channels, then avg ref
% all good chans
EEG.data = EEG.data*1e9;% used to make mean RMS = 86.5 for full 807 chan grid
%EEG.data = EEG.data*5e8;% makes mean RMS = 38.4 for 807, which is close to rms of grid
%EEG.data = EEG.data*1e3;% makes mean RMS = 22.8 for 248 chan grid, this time got 127 ICs
mean(rms(EEG.data'))
EEG = pop_saveset( EEG, 'filename',dset,'filepath',[forwardir]);
% sub-sample channels and run ICA:
numchans = 128;
[subset idx pos] = loc_subsets(EEG.chanlocs, numchans, 0, 0);
EEG = pop_select(EEG,'channel',subset{1});
EEG = pop_saveset( EEG, 'filename','GridForward128chan582-11-13.set','filepath',[forwardir]);
 
% Run AMICA:
maxiter = 3000;  %'numprocs',4-16, 'ppernode',200, 'max_threads',1 (no hanging, but slower)
num_models = 1;
amicadir = [forwardir,'amicaScalp207Grid807-582bp'];
%amicadir = [forwardir,'amicaScalp32Grid807-582bp'];
amicadir = [forwardir,'amicaScalp64Grid807-582bp'];
amicadir = [forwardir,'amicaScalp128Grid807-582bp'];
 
runamica17_nsg(EEG,'numprocs',4, 'max_threads',1, 'ppernode',25,'num_models',num_models,'batch',1,'outdir',amicadir,'lrate',0.002,'newtrate',0.5,'newt_start',num_models*50,'block_size',96,'pcakeep',size(EEG.data,1)-1,'do_reject',1,'max_iter',maxiter)
 
 
%% Load finalized scalp data with ICA:
dsets = {'GridForward582-11-13.set','GridForward128chan582-11-13.set','GridForward64chan582-11-13.set'};
adirs = {[forwardir,'amicaScalp207Grid807-582bp'],[forwardir,'amicaScalp128Grid807-582bp'],[forwardir,'amicaScalp64Grid807-582bp']};
for f=1:length(dsets)
    EEG = pop_loadset('filename',dsets{f},'filepath',[forwardir]);%% HP, then rm channels, then avg ref
    % load amica output:
    amicadir= adirs{f};
    mods = loadmodout15([amicadir]);
    EEG.etc.amica  = mods;mod=1;
    EEG.icaweights = EEG.etc.amica.W(:,:,mod);
    EEG.icasphere  = EEG.etc.amica.S(1:size(EEG.etc.amica.W,1),:);
    EEG.icawinv    = EEG.etc.amica.A(:,:,mod);EEG.icaact     = [];
    EEG            = eeg_checkset(EEG);
    EEG.icaact     = eeg_getica(EEG);
    %EEG = pop_saveset( EEG, 'filename',dsets{f},'filepath',[forwardir]);
 
    % pg=1;
    % for c=0:16:size(EEG.icawinv,2)
    %     pop_topoplot(EEG, 0, [c+1:c+15] ,dsets{f}(1:end-4),[4 4] ,0,'electrodes','off');
    %     pg=pg+1;
    %     str = ['print ',savedir,'ScalpTopoplots807grid_',int2str(pg+1),'.jpg -djpeg']; eval(str);
    % end;
 
    % do dipfit coreg and fit all dipoles
    EEG = pop_dipfit_settings( EEG, 'hdmfile','/expanse/projects/nemar/julie/eeglab2024.0/plugins/dipfit/standard_BEM/standard_vol.mat','mrifile','/expanse/projects/nemar/julie/eeglab2024.0/plugins/dipfit/standard_BEM/standard_mri.mat','chanfile','/expanse/projects/nemar/julie/eeglab2024.0/plugins/dipfit/standard_BEM/elec/standard_1005.elc','coordformat','MNI','coord_transform',[-0.50325 -19 -40.5366 -0.057007 0.044204 -1.5685 1.0562 1.0157 1.45] );
    EEG = pop_multifit(EEG, [1:size(EEG.icawinv,2)] ,'threshold',100,'plotopt',{'normlen','on'});
    EEG = pop_saveset( EEG, 'filename',dsets{f},'filepath',[forwardir]);
end;
% Plot dipoles:--
figure;hold on;
for ds=1:length(dsets)
    EEG = pop_loadset('filename',dsets{ds},'filepath',[forwardir]);%%
 
    % plot dipoles:
    ics = [1:size(EEG.icaact,1)];
    rvs = round(100*cell2mat({EEG.dipfit.model(ics).rv}));
    %plot(sort(rvs)); hold on;
    %str = ['print ',forwardir,'RVsScalpMontages.jpg -djpeg'];eval(str)
    [v idx] = sort(rvs);
    icnum(ds,:) = idx(1:31);
%sbplot(2,2,ds);
plot(sort(rvs),'linewidth',2);set(gca,'ylim',[0 55]);
%pop_topoplot(EEG, 0, [icnum(1,1:30)] ,EEG.filename,[] ,0,'electrodes','off');
end;
ylabel('Residual Variance');xlabel('Sorted ICs');set(gca,'fontsize',14);
set(gca,'xlim',[0 208]); set(gca,'ygrid','on');
legend({'207-Chan','128-chan','64-chan'});
title(['Scalp IC RVs']);
str = ['print ',forwardir,'SortedRVs-AllDecomps.jpg -djpeg'];eval(str)
 
cols = hot(7);cols(end+1:end+3,:) = [cols(end,:);cols(end,:);cols(end,:)];
ics = [];colcell = cell(1,0);
for c = 1:size(EEG.icaact,1)
    if rvs(c) <=10
        colcell{end+1} = cols(end-(rvs(c)-1),:);
        ics = [ics,c];
    end;   
end;   
figure;row=2;col = 2;rvr = 10;
sbplot(row,col,1);
[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'view',[0 0 1],'rvrange',rvr,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','on','color',colcell,'coordformat',EEG.dipfit.coordformat);
sbplot(row,col,2);
[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'view',[1 0 0],'rvrange',rvr,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','on','color',colcell,'coordformat',EEG.dipfit.coordformat);
sbplot(row,col,3);
[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'view',[0 -1 0],'rvrange',rvr,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','on','color',colcell,'coordformat',EEG.dipfit.coordformat);
sbplot(row,col,4);
[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'projlines','on','rvrange',rvr,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','on','color',colcell,'coordformat',EEG.dipfit.coordformat);
h=textsc('Dipoles with less than 10% RV (dark red to white = largest to smallest RV)')
set(h,'color','w');
str = ['print ',forwardir,'64chan_RV10percDipoles.jpg -djpeg'];eval(str)
%str = ['print ',savedir,'DelICsDipoles.jpg -djpeg'];eval(str)
figure;[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'projlines','off','rvrange',rvr,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','off','projimg','on','color',{'b'},'coordformat',EEG.dipfit.coordformat);
str = ['print ',savedir,'947changrid_DipolesRV12-Proj.jpg -djpeg'];eval(str)
%str = ['print ',savedir,'DelICsDipolesRV12-Proj.jpg -djpeg'];eval(str)
figure;[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'projlines','off','rvrange',10,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','off','projimg','on','color',{'b'},'coordformat',EEG.dipfit.coordformat);
str = ['print ',savedir,'947changrid_DipolesRV10-Proj.jpg -djpeg'];eval(str)
%str = ['print ',savedir,'DelICsDipolesRV10-Proj.jpg -djpeg'];eval(str)
figure;[sources realX realY realZ XE YE ZE] = dipplot(EEG.dipfit.model(ics) ,'projlines','off','rvrange',5,'dipolelength',0,'dipolesize',30,'normlen','on','gui','off','image','mri','spheres','off','projimg','on','color',{'b'},'coordformat',EEG.dipfit.coordformat);
str = ['print ',savedir,'947changrid_DipolesRV5-Proj.jpg -djpeg'];eval(str)